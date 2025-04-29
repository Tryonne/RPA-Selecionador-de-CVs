import os
import shutil
import spacy
import PyPDF2
import docx
from pathlib import Path
from typing import Dict, List, Tuple

# Department keywords
DEPARTMENTS = {
    "Engenharia de Software": [
        "python", "javascript", "sql", "desenvolvimento", "api", 
        "backend", "frontend", "java", "c#", "php", "react",
        "node", "git", "devops", "aws", "docker"
    ],
    "Marketing Digital": [
        "seo", "ads", "google analytics", "instagram", "campanhas",
        "copywriting", "social media", "marketing digital", "facebook",
        "linkedin", "content", "inbound", "outbound"
    ],
    "Recursos Humanos": [
        "recrutamento", "entrevista", "folha de pagamento", "formação",
        "benefícios", "gestão de pessoas", "treinamento", "seleção",
        "desenvolvimento organizacional", "cargos e salários"
    ],
    "Suporte Técnico": [
        "help desk", "ticket", "atendimento", "resolução de problemas",
        "hardware", "suporte", "service desk", "infraestrutura",
        "manutenção", "redes", "sistemas operacionais"
    ]
}

class CVOrganizer:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.nlp = spacy.load("pt_core_news_sm")
        self.setup_directories()

    def setup_directories(self):
        """Create output directories for each department"""
        for department in DEPARTMENTS.keys():
            department_dir = self.output_dir / department
            department_dir.mkdir(parents=True, exist_ok=True)

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return text

    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        text = ""
        try:
            doc = docx.Document(file_path)
            text = " ".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
        return text

    def analyze_cv(self, text: str) -> Tuple[str, float]:
        """Analyze CV content and determine the best matching department"""
        scores = {}
        doc = self.nlp(text.lower())
        
        for department, keywords in DEPARTMENTS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    score += 1
            scores[department] = score

        best_department = max(scores.items(), key=lambda x: x[1])
        return best_department

    def process_cv(self, file_path: Path):
        """Process individual CV file"""
        if file_path.suffix.lower() == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self.extract_text_from_docx(file_path)
        else:
            print(f"Unsupported file format: {file_path}")
            return

        department, score = self.analyze_cv(text)
        if score > 0:
            destination = self.output_dir / department / file_path.name
            shutil.copy2(file_path, destination)
            print(f"Moved {file_path.name} to {department}")
        else:
            print(f"Could not classify {file_path.name}")

    def organize_cvs(self):
        """Main method to organize all CVs in the input directory"""
        for file_path in self.input_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
                self.process_cv(file_path)

def main():
    input_dir = "input_cvs"
    output_dir = "organized_cvs"
    
    organizer = CVOrganizer(input_dir, output_dir)
    organizer.organize_cvs()

if __name__ == "__main__":
    main()