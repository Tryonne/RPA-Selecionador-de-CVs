import os
import json
import shutil
import spacy
import PyPDF2
import docx
from pathlib import Path
from typing import Dict, List, Tuple

class CVOrganizer:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.nlp = spacy.load("pt_core_news_sm")
        self.departments = self._load_departments()
        self.create_department_folders()

    def _load_departments(self) -> Dict[str, List[str]]:
        config_file = Path(__file__).parent / "departments.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Erro: departments.json não foi encontrado!")
            return {}

    def create_department_folders(self):
        for department_name in self.departments:
            folder_path = self.output_dir / department_name
            folder_path.mkdir(parents=True, exist_ok=True)
        
        unclassified_folder = self.output_dir / "Não Classificado"
        unclassified_folder.mkdir(parents=True, exist_ok=True)

    def read_pdf(self, file_path: Path) -> str:
        try:
            with open(file_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                return ' '.join(page.extract_text() for page in pdf.pages)
        except Exception as error:
            print(f"Não foi possível ler o PDF {file_path}: {error}")
            return ""

    def read_word(self, file_path: Path) -> str:
        try:
            doc = docx.Document(file_path)
            return ' '.join(paragraph.text for paragraph in doc.paragraphs)
        except Exception as error:
            print(f"Não foi possível ler o Word {file_path}: {error}")
            return ""

    def find_best_department(self, cv_text: str) -> tuple[str, int]:
        cv_text = cv_text.lower()
        department_scores = {}

        for department, keywords in self.departments.items():
            matches = 0
            for keyword in keywords:
                if keyword.lower() in cv_text:
                    matches += 1
            score_percentage = (matches / len(keywords)) * 100
            department_scores[department] = score_percentage

        best_match = max(department_scores.items(), key=lambda x: x[1])
        
        if best_match[1] < 15:
            return ("Não Classificado", 0)
        return best_match

    def process_single_cv(self, file_path: Path):
        if file_path.suffix.lower() == '.pdf':
            cv_text = self.read_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            cv_text = self.read_word(file_path)
        else:
            print(f"Tipo do ficheito não suportado: {file_path.suffix}")
            return

        if not cv_text:
            print(f"Não foi possível ler o ficheiro: {file_path.name}")
            return

        department, score = self.find_best_department(cv_text)
        new_location = self.output_dir / department / file_path.name
        shutil.copy2(file_path, new_location)
        
        if department != "Não Classificado":
            print(f"✓ Movido {file_path.name} para {department} pasta (Score: {score:.1f}%)")
        else:
            print(f"× Movido para Não Classificado: {file_path.name}")

    def organize_cvs(self):
        supported_formats = ['.pdf', '.docx', '.doc']
        
        for file_path in self.input_dir.glob("*.*"):
            if file_path.suffix.lower() in supported_formats:
                self.process_single_cv(file_path)

def main():
    input_dir = "bau_dos_cvs"
    output_dir = "cvs_organizados"
    
    organizer = CVOrganizer(input_dir, output_dir)
    organizer.organize_cvs()

if __name__ == "__main__":
    main()