import customtkinter as ctk
import tkinter as tk
from datetime import datetime
import sqlite3
import db_ai_report
import os
import requests
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import threading
import time

class AdminAIReport(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Enhanced color scheme
        self.theme_color = "#E6E6FA"  # Lavender background
        self.button_color = "#9370DB"  # Medium Purple
        self.button_hover_color = "#8A2BE2"  # Blue Violet
        self.accent_color = "#F0E6FF"  # Light purple for cards
        self.text_color = "#4B0082"  # Dark purple
        self.highlight_color = "#DCD0FF"  # Highlight purple
        
        self.configure(fg_color=self.theme_color)
        # Create reports directory if it doesn't exist
        self.reports_dir = "ai_reports"
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
            
        self.setup_ui()
        self.update_latest_report_info()

        self.API_BASE_URL = "https://api.dify.ai/v1"
        self.API_KEY = self.get_api_key_from_db()

    def get_total_feedback(self):
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total = cursor.fetchone()[0]
            conn.close()
            return str(total)
        except Exception as e:
            print(f"Database error: {e}")
            return "N/A"

    def setup_ui(self):
        # Top banner
        banner = ctk.CTkFrame(self, fg_color=self.highlight_color, height=80)
        banner.pack(fill="x", pady=(0, 40))
        banner.pack_propagate(False)
        
        banner_label = ctk.CTkLabel(
            banner,
            text="AI Feedback Analysis Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.text_color
        )
        banner_label.pack(side="left", padx=50, pady=15)

        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=50, pady=(0, 40))
        
        # Left column (60% width)
        left_column = ctk.CTkFrame(main_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 30))
        
        # Right column (40% width)
        right_column = ctk.CTkFrame(main_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True)

        # === Left Column Contents ===
        # Stats Panel
        stats_panel = ctk.CTkFrame(left_column, fg_color=self.accent_color, corner_radius=20)
        stats_panel.pack(fill="x", pady=(0, 40))
        
        total_feedback = self.get_total_feedback()
        self.create_stat_box(stats_panel, "Total Feedback Collected", total_feedback, "Responses analyzed by AI")
        
        # Report Preview Frame
        preview_frame = ctk.CTkFrame(left_column, fg_color=self.accent_color, corner_radius=20)
        preview_frame.pack(fill="both", expand=True)
        
        preview_header = ctk.CTkFrame(preview_frame, fg_color=self.highlight_color, corner_radius=20)
        preview_header.pack(fill="x", padx=3, pady=3)
        
        preview_label = ctk.CTkLabel(
            preview_header,
            text="📊 Generated Reports",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.text_color
        )
        preview_label.pack(pady=20)

        # Create scrollable frame for report list
        self.reports_list_frame = ctk.CTkScrollableFrame(
            preview_frame,
            fg_color="transparent",
            height=500
        )
        self.reports_list_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Load initial report list
        self.refresh_reports_list()

        # === Right Column Contents ===
        # Report Structure Card
        structure_card = ctk.CTkFrame(right_column, fg_color=self.accent_color, corner_radius=20)
        structure_card.pack(fill="x", pady=(0, 40))
        
        structure_header = ctk.CTkFrame(structure_card, fg_color=self.highlight_color, corner_radius=20)
        structure_header.pack(fill="x", padx=3, pady=3)
        
        structure_label = ctk.CTkLabel(
            structure_header,
            text="📑 Report Structure",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.text_color
        )
        structure_label.pack(pady=20)

        structure_text = """
1. EXECUTIVE SUMMARY
   • Concise overview of all feedback
   • Highlight of critical issues
   • System impact assessment

2. DETAILED ANALYSIS
   • Key Findings
   • Areas of Concern
   • Suggested Improvements
        """
        structure_content = ctk.CTkLabel(
            structure_card,
            text=structure_text,
            font=ctk.CTkFont(size=18),
            justify="left",
            text_color=self.text_color
        )
        structure_content.pack(padx=30, pady=30)

        # Download Section
        download_frame = ctk.CTkFrame(right_column, fg_color=self.accent_color, corner_radius=20)
        download_frame.pack(fill="x")
        
        download_header = ctk.CTkFrame(download_frame, fg_color=self.highlight_color, corner_radius=20)
        download_header.pack(fill="x", padx=3, pady=3)
        
        download_label = ctk.CTkLabel(
            download_header,
            text="⬇️ Generate Report",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.text_color
        )
        download_label.pack(pady=20)

        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(download_frame, height=15)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=30, pady=(30,0))
        self.progress_bar.pack_forget()

        download_button = ctk.CTkButton(
            download_frame,
            text="Download Analysis Report",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=60,
            command=self.download_report,
            fg_color=self.button_color,
            hover_color=self.button_hover_color
        )
        download_button.pack(pady=30)

        self.timestamp_label = ctk.CTkLabel(
            download_frame,
            text="Last Report: Never",
            font=ctk.CTkFont(size=16),
            text_color=self.text_color
        )
        self.timestamp_label.pack(pady=(0, 30))

    def create_stat_box(self, parent, title, value, subtitle):
        padding = 40
        stat_box = ctk.CTkFrame(parent, fg_color="transparent")
        stat_box.pack(padx=padding, pady=padding)
        
        value_label = ctk.CTkLabel(
            stat_box,
            text=value,
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color=self.text_color
        )
        value_label.pack()
        
        title_label = ctk.CTkLabel(
            stat_box,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.text_color
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            stat_box,
            text=subtitle,
            font=ctk.CTkFont(size=18),
            text_color=self.text_color
        )
        subtitle_label.pack()

    def simulate_progress(self):
        import time
        self.progress_bar.pack(padx=20, pady=(20,0))
        for i in range(101):
            self.progress_bar.set(i / 100)
            self.update()
            time.sleep(0.01)
        self.progress_bar.pack_forget()

    def update_latest_report_info(self):
        """Update the timestamp label with the latest report information"""
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT reportID, reportFilePath, time 
                FROM aiReport 
                ORDER BY time DESC 
                LIMIT 1
            """)
            latest_report = cursor.fetchone()
            
            if latest_report:
                report_id, filepath, timestamp = latest_report
                self.timestamp_label.configure(text=f"Last Report: {timestamp}")
            else:
                self.timestamp_label.configure(text="Last Report: Never")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.timestamp_label.configure(text="Last Report: Error")
        finally:
            if conn:
                conn.close()

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

    def download_report(self):
        # Get feedback data first
        feedback_data = self.get_feedback_data()
        
        # Start progress bar and API call in parallel
        self.progress_bar.pack(padx=20, pady=(20,0))
        self.progress_bar.set(0)
        
        # Create a flag to track API completion
        self.api_response_ready = False
        self.analysis_result = None
        
        # Start API call in a separate thread
        api_thread = threading.Thread(
            target=self.get_analysis_in_background,
            args=(feedback_data,)
        )
        api_thread.start()
        
        # Start progress bar animation
        self.simulate_progress_and_wait()

    def get_analysis_in_background(self, feedback_data):
        """Run the API call in background and store result"""
        self.analysis_result = self.generate_analysis(feedback_data)
        self.api_response_ready = True

    def simulate_progress_and_wait(self):
        """Run progress bar for 20 seconds and wait for API response"""
        start_time = time.time()
        duration = 20.0  # 20 seconds
        normal_speed_delay = 0.05  # Normal animation delay
        fast_speed_delay = 0.01  # 5x faster animation delay
        wait_threshold = 0.95  # 95% completion point (19 seconds)
        
        while (time.time() - start_time) < duration:
            # Calculate progress percentage
            elapsed = time.time() - start_time
            progress = elapsed / duration
            
            # If we're at 95% and API isn't ready, wait
            if progress >= wait_threshold and not self.api_response_ready:
                self.progress_bar.set(wait_threshold)
                self.update()
                # Wait for API response
                while not self.api_response_ready:
                    time.sleep(0.1)
                    self.update()
                # Once API is ready, quickly complete the bar
                for fast_step in range(int(wait_threshold * 100), 101):
                    self.progress_bar.set(fast_step / 100)
                    self.update()
                    time.sleep(fast_speed_delay)
                break
            
            # If API response is ready and we're not at 100% yet, speed up
            if self.api_response_ready and progress < 1.0:
                # Calculate remaining progress to cover
                remaining_progress = 1.0 - progress
                # Calculate shorter time to complete (5x faster)
                remaining_steps = int(remaining_progress * 100)  # Convert to percentage steps
                
                # Quickly complete the remaining progress
                for fast_step in range(remaining_steps):
                    fast_progress = progress + (fast_step * remaining_progress / remaining_steps)
                    self.progress_bar.set(fast_progress)
                    self.update()
                    time.sleep(fast_speed_delay)
                
                # Set to complete and break the main loop
                self.progress_bar.set(1.0)
                self.update()
                break
            
            # Normal speed progress
            self.progress_bar.set(progress)
            self.update()
            time.sleep(normal_speed_delay)
        
        # Ensure progress bar shows complete
        self.progress_bar.set(1.0)
        self.update()
        
        # Wait for API response if it's still not ready
        while not self.api_response_ready:
            time.sleep(0.1)
            self.update()
        
        # Hide progress bar
        self.progress_bar.pack_forget()
        
        # Now that we have both progress bar completion and API response, proceed with PDF
        if self.analysis_result:
            self.save_analysis_as_pdf(None, self.analysis_result)

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
                    dt = datetime.fromisoformat(timestamp)
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
            current_time = datetime.now()
            content.append(Paragraph(
                f"Generated on: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
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
                
                # Store the report information in the database
                try:
                    conn = sqlite3.connect('properties.db')
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO aiReport (reportFilePath, time)
                        VALUES (?, ?)
                    """, (filename, current_time.strftime('%Y-%m-%d %H:%M:%S')))
                    
                    conn.commit()
                    
                    # Update the timestamp label and refresh reports list
                    self.update_latest_report_info()
                    self.refresh_reports_list()
                    
                except sqlite3.Error as db_error:
                    print(f"Database error while storing report: {db_error}")
                finally:
                    if conn:
                        conn.close()
                
            except Exception as e:
                raise Exception(f"Error building PDF: {str(e)}")
            
        except Exception as e:
            error_msg = f"Error generating PDF: {str(e)}"
            print(error_msg)  # Print to console for debugging

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

    def generate_report_content(self):
        """Generate the content for the AI report"""
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            
            # Get feedback statistics
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = cursor.fetchone()[0]
            
            # Get feedback by category
            cursor.execute("SELECT category, COUNT(*) FROM feedback GROUP BY category")
            category_stats = cursor.fetchall()
            
            # Generate report content
            content = f"""EXECUTIVE SUMMARY
Total Feedback Collected: {total_feedback}

DETAILED ANALYSIS

1. Feedback Categories:
"""
            for category, count in category_stats:
                percentage = (count / total_feedback) * 100 if total_feedback > 0 else 0
                content += f"   • {category}: {count} ({percentage:.1f}%)\n"

            content += "\n2. Key Findings:\n"
            content += "   • Analysis of user feedback patterns\n"
            content += "   • Identification of common themes\n"
            content += "   • Trending topics in user comments\n"

            content += "\n3. Recommendations:\n"
            content += "   • Continue monitoring user feedback\n"
            content += "   • Address common concerns\n"
            content += "   • Implement suggested improvements\n"

            return content
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "Error generating report content"
            
        finally:
            if conn:
                conn.close()

    def refresh_reports_list(self):
        """Refresh the list of reports in the preview"""
        # Clear existing widgets in the reports list frame
        for widget in self.reports_list_frame.winfo_children():
            widget.destroy()
        
        try:
            conn = sqlite3.connect('properties.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT reportID, reportFilePath, time 
                FROM aiReport 
                ORDER BY time DESC
            """)
            reports = cursor.fetchall()
            
            if not reports:
                no_reports_label = ctk.CTkLabel(
                    self.reports_list_frame,
                    text="No reports generated yet",
                    font=ctk.CTkFont(size=18),
                    text_color=self.text_color
                )
                no_reports_label.pack(pady=25)
            else:
                for report_id, filepath, timestamp in reports:
                    # Get just the filename from the full path
                    filename = os.path.basename(filepath)
                    
                    # Create frame for each report entry
                    report_entry = ctk.CTkFrame(
                        self.reports_list_frame,
                        fg_color=self.highlight_color,
                        corner_radius=15
                    )
                    report_entry.pack(fill="x", padx=8, pady=8)
                    
                    # Create a container for the text information
                    text_container = ctk.CTkFrame(
                        report_entry,
                        fg_color="transparent"
                    )
                    text_container.pack(side="left", fill="x", expand=True, padx=15, pady=15)
                    
                    # Add report ID and timestamp
                    report_info = ctk.CTkLabel(
                        text_container,
                        text=f"Report #{report_id}\nGenerated: {timestamp}",
                        font=ctk.CTkFont(size=16),
                        text_color=self.text_color,
                        justify="left"
                    )
                    report_info.pack(anchor="w")
                    
                    # Add filename below
                    filename_label = ctk.CTkLabel(
                        text_container,
                        text=f"File: {filename}",
                        font=ctk.CTkFont(size=14),
                        text_color=self.text_color,
                        justify="left"
                    )
                    filename_label.pack(anchor="w", pady=(5, 0))
                    
                    # Add open button
                    open_button = ctk.CTkButton(
                        report_entry,
                        text="Open Report",
                        font=ctk.CTkFont(size=16),
                        width=120,
                        height=40,
                        fg_color=self.button_color,
                        hover_color=self.button_hover_color,
                        command=lambda fp=filepath: self.open_report(fp)
                    )
                    open_button.pack(side="right", padx=15, pady=15)
                    
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                self.reports_list_frame,
                text=f"Error loading reports: {e}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            if conn:
                conn.close()

    def open_report(self, filepath):
        """Open the selected report PDF"""
        try:
            import os
            import platform
            import subprocess
            
            if not os.path.exists(filepath):
                print(f"Error: File not found - {filepath}")
                return
                
            if platform.system() == 'Darwin':       # macOS
                subprocess.run(['open', filepath])
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # Linux variants
                subprocess.run(['xdg-open', filepath])
                
        except Exception as e:
            print(f"Error opening file: {e}")

def show_admin_ai_report(root, home_frame, show_dashboard_callback):
    # Hide home frame
    home_frame.pack_forget()
    
    # Create main frame for AI report
    report_frame = ctk.CTkFrame(root, fg_color="#E6E6FA")
    report_frame.pack(fill="both", expand=True)
    
    def back_to_home():
        # Hide report frame and call the dashboard callback
        report_frame.pack_forget()
        show_dashboard_callback()
    
    # Add back button at the top
    back_btn = ctk.CTkButton(
        master=report_frame,
        text="← Back",
        command=back_to_home,
        width=100,
        height=30,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    back_btn.pack(anchor="nw", padx=20, pady=10)
    
    # Create the AdminAIReport instance with the report_frame
    app = AdminAIReport(report_frame)
    app.pack(fill="both", expand=True)
    
    # Create AI report table
    db_ai_report.create_ai_report_table()

def main():
    # Create the AI report table when running independently
    db_ai_report.create_ai_report_table()
    
    root = ctk.CTk()
    root.title("Admin AI Report")
    root.geometry("1920x1080")
    
    # Create home frame (white page)
    home_frame = ctk.CTkFrame(master=root, fg_color="white")
    home_frame.pack(fill="both", expand=True)
    
    # Add switch button to home frame
    switch_btn = ctk.CTkButton(
        master=home_frame,
        text="Open AI Report",
        command=lambda: show_admin_ai_report(root, home_frame, lambda: show_dashboard(root, home_frame)),
        width=200,
        height=50,
        fg_color="#9370DB",
        hover_color="#7B68EE"
    )
    switch_btn.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()