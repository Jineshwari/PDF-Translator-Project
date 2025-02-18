# PDF Translator

A Django-based web application that enables users to upload PDFs, apply find-and-replace translations, and download modified versions while preserving the original document structure. Built with PyMuPDF (fitz) for PDF processing.

## ✨ Features

- **Upload & Translate PDFs**: Modify text based on predefined dictionaries
- **Database-Driven Dictionary**: Custom word replacement via database entries
- **Preserve PDF Formatting**: Ensures original layout remains intact
- **Interactive Editor**: Manually adjust text before downloading

## 🚀 Installation

1. Clone the Repository
```bash
git clone https://github.com/yourusername/PDF-Translator.git
cd PDF-Translator
```

2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Set Up Environment Variables
Create a `.env` file in the root directory and add:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=your-database-url
```

5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

## 📁 Project Structure
```
PDF-Translator/
├── media/            # (Ignored) Stores uploaded PDFs
├── static/           # CSS, JS, and images
├── templates/        # HTML files
├── your_app/        # Django app logic
├── db.sqlite3       # (Ignored) Local database
├── manage.py        # Django project manager
├── requirements.txt # Project dependencies
├── .gitignore      # Files ignored by Git
└── .env            # (Ignored) Secret keys & configs
```

## 🔍 Usage

1. Upload a PDF and select a translation dictionary
2. Preview the modified PDF and manually adjust text if needed
3. Download the translated PDF


## 📞 Contact

- **Developer**: Jineshwari
- **Email**: bagul.jineshwari@gmail.com
- **GitHub**: Jineshwari

## ✨ Happy Coding! 🚀
