import customtkinter as ctk
import datetime
import requests
import json
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tkinter import filedialog

class ChatbotInterface:
    def __init__(self):
        # API Configuration
        self.API_BASE_URL = "https://api.dify.ai/v1"
        self.API_KEY = self.get_api_key_from_db()
        
        # Configure the appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create the main window
        self.window = ctk.CTk()
        self.window.title("AI Report Generator")
        self.window.geometry("300x100")  # Smaller window size

        # Create the main container
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create download button
        self.download_button = ctk.CTkButton(
            self.main_container,
            text="Download Feedback Report",
            command=self.generate_and_save_report
        )
        self.download_button.pack(expand=True)

    def generate_and_save_report(self):
        # Get feedback data
        feedback_data = self.get_feedback_data()
        
        # Generate analysis using API
        analysis = self.generate_analysis(feedback_data)
        
        if analysis:
            self.save_analysis_as_pdf(feedback_data, analysis)

    def get_feedback_data(self):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, category, comment, timestamp 
                FROM feedback 
                ORDER BY timestamp DESC
            """)
            
            feedback_entries = cursor.fetchall()
            
            if not feedback_entries:
                return "No feedback data available"
            
            report_lines = []
            
            for entry in feedback_entries:
                id, category, comment, timestamp = entry
                try:
                    dt = datetime.datetime.fromisoformat(timestamp)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_time = timestamp
                
                entry_text = [
                    f"Feedback #{id}",
                    f"Category: {category}",
                    f"Comment: {comment}",
                    f"Time: {formatted_time}",
                    "-" * 40,
                    ""
                ]
                report_lines.extend(entry_text)
            
            report_lines.extend([
                f"Total Feedback Entries: {len(feedback_entries)}",
                "",
                "Categories Breakdown:"
            ])
            
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM feedback 
                GROUP BY category
            """)
            categories = cursor.fetchall()
            
            for category, count in categories:
                report_lines.append(f"  {category}: {count}")
            
            return "\n".join(report_lines)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return f"Database error: {e}"
        finally:
            if conn:
                conn.close()

    def generate_analysis(self, feedback_data):
        feedback_analysis_prompt = f"""As a government stall rental system analyst, analyze this feedback data and provide:

{feedback_data}

Please structure your response as follows:

1. EXECUTIVE SUMMARY (Maximum 100 words):
   Provide a concise overview of all feedback, highlighting the most critical issues and their impact on the system.

2. DETAILED ANALYSIS:
   - Key findings
   - Areas of concern
   - Suggested improvements

Format your response in clear sections with bullet points. Make the executive summary brief but comprehensive enough for administrators to grasp the overall situation quickly."""
        
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": {},
            "query": feedback_analysis_prompt,
            "user": "user-1",
            "response_mode": "blocking"
        }

        try:
            response = requests.post(
                f"{self.API_BASE_URL}/chat-messages",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get('answer', '')
            else:
                print(f"Error generating analysis: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    # Rest of the methods remain the same
    def get_api_key_from_db(self):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("SELECT api_key FROM systemInformation ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
            else:
                print("Error: No API key found in database. Please set up the API key in admin settings.")
                return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def save_analysis_as_pdf(self, feedback_data, analysis):
        try:
            # Get save location from user
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Feedback Analysis Report"
            )
            
            if not filename:
                print("PDF generation cancelled")
                return

            # Create the PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Define styles
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                keepWithNext=True
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceBefore=6,
                spaceAfter=6
            )

            # Build content
            content = []

            # Add title
            content.append(Paragraph(
                "Government Stall Rental System - Analysis Report",
                title_style
            ))
            
            # Add timestamp
            content.append(Paragraph(
                f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                normal_style
            ))
            content.append(Spacer(1, 20))

            # Process analysis text
            current_section = None
            for line in analysis.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Handle different types of lines
                    if line.startswith('**') and line.endswith('**'):
                        # Section headers
                        header_text = line.strip('*').strip()
                        content.append(Paragraph(header_text, heading_style))
                        current_section = header_text
                    elif line.startswith('•') or line.startswith('-'):
                        # Bullet points
                        bullet_text = line[1:].strip()
                        # Handle bold text within bullet points
                        bullet_text = self._convert_bold_text_for_pdf(bullet_text)
                        content.append(Paragraph(
                            f"• {bullet_text}",
                            normal_style
                        ))
                    else:
                        # Regular text with possible bold sections
                        line = self._convert_bold_text_for_pdf(line)
                        content.append(Paragraph(line, normal_style))
                except Exception as e:
                    print(f"Error processing analysis line: {e}")
                    continue

            # Build the PDF
            try:
                doc.build(content)
                print(f"Analysis report successfully saved to: {filename}")
            except Exception as e:
                raise Exception(f"Error building PDF: {str(e)}")
            
        except Exception as e:
            error_msg = f"Error generating PDF: {str(e)}"
            print(error_msg)  # Print to console for debugging

    # Add this new helper method to the class
    def _convert_bold_text_for_pdf(self, text):
        """Convert markdown bold syntax to PDF bold tags"""
        # Handle bold text marked with double asterisks
        while "**" in text:
            start = text.find("**")
            end = text.find("**", start + 2)
            if end != -1:
                # Replace markdown bold with PDF bold tags
                bold_text = text[start+2:end]
                text = text[:start] + f"<b>{bold_text}</b>" + text[end+2:]
            else:
                break
        return text

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ChatbotInterface()
    app.run()
