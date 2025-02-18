import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from .models import Dictionary, WordPair
import fitz 

def upload_pdf(request):
    if request.method == 'POST':
        # Handle file upload
        if 'pdf_file' in request.FILES:
            pdf_file = request.FILES['pdf_file']
            dictionary_id = request.POST.get('dictionary_id')

            # Save the uploaded file
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            uploaded_file_path = fs.save(pdf_file.name, pdf_file)
            uploaded_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file_path)

            # Fetch the dictionary and word pairs
            try:
                dictionary = Dictionary.objects.get(id=dictionary_id)
                word_pairs = dictionary.word_pairs.all()
                replacements = {pair.find_word: pair.replace_word for pair in word_pairs}
            except Dictionary.DoesNotExist:
                return HttpResponse("Selected dictionary not found.", status=400)

            # Process the PDF with the new logic
            modified_pdf_path = os.path.join(
                settings.MEDIA_ROOT, f"modified_{os.path.basename(uploaded_file_path)}"
            )
            replace_text_in_pdf(uploaded_file_path, modified_pdf_path, replacements)

            # Store modified PDF path in the session
            request.session['modified_pdf_path'] = modified_pdf_path

            # Render the modify page for user review
            modified_pdf_url = settings.MEDIA_URL + os.path.basename(modified_pdf_path)
            print(f"Modified PDF Path: {modified_pdf_path}")  # Debugging
            print(f"Modified PDF URL: {modified_pdf_url}")  # Debugging
            
            return render(request, 'modify.html', {
                'modified_pdf': os.path.basename(modified_pdf_path),
                'dictionary': dictionary,
                'modified_pdf_url': modified_pdf_url,
            })

        

        elif 'find_word' in request.POST and 'replace_word' in request.POST:
            # Handle find-and-replace logic on the modified PDF
            find_word = request.POST.get('find_word')
            replace_word = request.POST.get('replace_word')
            dictionary_id = request.POST.get('dictionary_id')
            modified_pdf_path = request.session.get('modified_pdf_path', None)

            # Update the dictionary with new word pair
            try:
                dictionary = Dictionary.objects.get(id=dictionary_id)
                word_pair, created = WordPair.objects.get_or_create(
                    dictionary=dictionary, find_word=find_word
                )
                word_pair.replace_word = replace_word
                word_pair.save()
            except Dictionary.DoesNotExist:
                return HttpResponse("Selected dictionary not found.", status=400)

            if not modified_pdf_path:
                return HttpResponse("Modified PDF path is not provided.", status=400)

            # Apply the new find-and-replace to the PDF
            updated_pdf_path = os.path.join(
                settings.MEDIA_ROOT, f"updated_{os.path.basename(modified_pdf_path)}"
            )
            replace_text_in_pdf(modified_pdf_path, updated_pdf_path, {find_word: replace_word})

            # Update the session with the latest modified PDF path
            request.session['modified_pdf_path'] = updated_pdf_path

            # Render the updated PDF for review
            return render(request, 'modify.html', {
                'modified_pdf': os.path.basename(updated_pdf_path),
                'dictionary': dictionary,
                'modified_pdf_url': settings.MEDIA_URL + os.path.basename(updated_pdf_path),
            })

    # Display upload form with dictionaries
    dictionaries = Dictionary.objects.all()
    return render(request, 'upload.html', {'dictionaries': dictionaries})


from django.http import FileResponse

def download_pdf(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=False, content_type='application/pdf')
    return HttpResponse("File not found.", status=404)

# New logic for replacing text in PDF
def replace_text_in_pdf(pdf_path, output_path, replacements):
    document = fitz.open(pdf_path)

    for page_num in range(len(document)):
        page = document.load_page(page_num)

        for old_text, new_text in replacements.items():
            # Find original font size for this text
            original_font_size = find_original_font_size(page, old_text)

            areas = page.search_for(old_text)

            for area in areas:
                # Adjust bbox height to match original text height
                adjusted_bbox = fitz.Rect(
                    area.x0,
                    area.y0 + 1,
                    area.x1,
                    area.y1 - 1
                )

                # Detect background color by sampling slightly below the text
                bg_color = detect_fill_color(page, adjusted_bbox)

                # Get original bounding box details
                original_width = adjusted_bbox.width

                # Calculate font size
                if len(new_text) <= len(old_text):
                    # If new text is same or smaller, use original font size
                    font_size = original_font_size
                else:
                    # If new text is larger, reduce font size to fit
                    font_size = original_font_size * (len(old_text) / len(new_text))

                new_text_width = fitz.get_text_length(new_text, fontsize=font_size)

                # Adjust font size further if it's still too big
                while new_text_width > original_width and font_size > 5:
                    font_size -= 1
                    new_text_width = fitz.get_text_length(new_text, fontsize=font_size)

                # Calculate x and y positioning
                x = adjusted_bbox.x0 + (original_width - new_text_width) / 2
                y = adjusted_bbox.y1 - 2  # Align to bottom of original text area

                # Erase old text with detected background color
                page.draw_rect(adjusted_bbox, color=bg_color, fill=bg_color)

                # Determine text color based on background
                text_color = (1.0, 1.0, 1.0) if bg_color == (0.0, 0.0, 0.0) else (0.0, 0.0, 0.0)

                # Insert new text
                page.insert_text((x, y), new_text, fontsize=font_size, color=text_color)
    try:
        document.save(output_path)
        document.close()
        print(f"Modified PDF saved as '{output_path}'")  # Debugging
    except Exception as e:
        print(f"Error saving PDF: {e}")  # Debugging
        return None


def detect_fill_color(page, bbox):
    drawings = page.get_drawings()

    offset_bbox = fitz.Rect(
        bbox.x0,
        bbox.y1 - 2,
        bbox.x1,
        bbox.y1 + 2
    )

    for drawing in drawings:
        if drawing['fill'] is not None:
            for item in drawing['items']:
                y0, y1 = item[1][1], item[1][3]
                if offset_bbox[1] > y0 and offset_bbox[1] < y1:
                    return drawing['fill']

    return (1.0, 1.0, 1.0)


def find_original_font_size(page, word):
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if word in span["text"]:
                    return span["size"]
    return 12  # Default font size if word not found


def add_dictionary(request):
    if request.method == 'POST':
        name = request.POST.get('dictionary_name')

        # Validate dictionary name
        if not name:
            return HttpResponse("Dictionary name is required.", status=400)

        # Create the dictionary
        dictionary = Dictionary.objects.create(name=name)

        # Loop through dynamic word pairs
        i = 0
        while True:
            find_word = request.POST.get(f'find_word_{i}')
            replace_word = request.POST.get(f'replace_word_{i}')

            # Break the loop if no more pairs are found
            if not find_word or not replace_word:
                break

            # Save the word pair to the database
            WordPair.objects.create(dictionary=dictionary, find_word=find_word, replace_word=replace_word)
            i += 1

        return redirect('upload_pdf')

    return HttpResponse("Invalid request method.", status=405)
