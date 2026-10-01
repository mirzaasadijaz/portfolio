#!/usr/bin/env python3
"""Build Asad Ijaz's one-page, ATS-friendly resume with an image."""
import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Flowable, Table, TableStyle, Image as RLImage)

OUT = sys.argv[1] if len(sys.argv) > 1 else "Asad_Ijaz_Data_Scientist_Resume.pdf"
IMG_PATH = "asad.jpg"  # <--- Ensure your square portrait image is named this in the same folder

# ---------- tunables (adjusted so the page is full but breathable) ----------
BODY = 10.2      # body font size
LEAD = 14.0      # body leading
SEC_GAP = 9.0    # space before each section heading
ITEM_GAP = 4.0   # space between experience / project entries

# ---------- premium corporate colours ----------
INK = HexColor("#0F172A")       # Slate 900 (Headings)
TEXT = HexColor("#334155")      # Slate 700 (Body text)
MUTED = HexColor("#475569")     # Slate 600 (Subtitles/Tags)
FAINT = HexColor("#CBD5E1")     # Slate 300 (Rules/Lines)
ACCENT = HexColor("#2563EB")    # Royal Blue 600
ACCENT_HEX = "#2563EB"

W, H = A4
LM = RM = 38
TM, BM = 30, 26
FW = W - LM - RM

# ---------- styles ----------
S = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=32, leading=36, textColor=INK, spaceAfter=2),
    "headline": ParagraphStyle("headline", fontName="Helvetica-Bold", fontSize=13.5, leading=16, textColor=ACCENT, spaceAfter=4),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=10, leading=14, textColor=MUTED),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=BODY, leading=LEAD, textColor=TEXT),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=BODY, leading=LEAD, textColor=TEXT,
                             leftIndent=14, firstLineIndent=-4, bulletIndent=3, spaceAfter=2.0,
                             bulletFontName="Helvetica-Bold", bulletFontSize=BODY+1, bulletColor=ACCENT),
    "skill": ParagraphStyle("skill", fontName="Helvetica", fontSize=BODY, leading=LEAD, textColor=TEXT, spaceAfter=2.5),
    "desc": ParagraphStyle("desc", fontName="Helvetica", fontSize=BODY, leading=LEAD, textColor=TEXT, spaceAfter=0),
}

# ---------- custom flowables ----------
class Section(Flowable):
    """Section heading: bold title, thin page rule, dynamic accent rule."""
    def __init__(self, title, size=13.5):
        super().__init__()
        self.title, self.size = title, size

    def wrap(self, aw, ah):
        self.aw = aw
        return aw, self.size + 8

    def draw(self):
        c = self.canv
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", self.size)
        c.drawString(0, 7, self.title)
        
        tw = stringWidth(self.title, "Helvetica-Bold", self.size)
        
        c.setStrokeColor(FAINT)
        c.setLineWidth(0.5)
        c.line(0, 2, self.aw, 2)
        
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.8)
        c.line(0, 2, tw + 6, 2)

class RoleLine(Flowable):
    """Title • Organisation ............ dates"""
    def __init__(self, title, org, dates, size=11.5):
        super().__init__()
        self.title, self.org, self.dates, self.size = title, org, dates, size

    def wrap(self, aw, ah):
        self.aw = aw
        return aw, self.size + 4

    def draw(self):
        c, s, y = self.canv, self.size, 3.5
        c.setFont("Helvetica-Bold", s)
        c.setFillColor(INK)
        c.drawString(0, y, self.title)
        x = stringWidth(self.title, "Helvetica-Bold", s) + 7
        
        c.setFont("Helvetica", s)
        c.setFillColor(ACCENT)
        c.drawString(x, y, "•")
        x += stringWidth("•", "Helvetica", s) + 7
        
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Oblique", s - 0.5)
        c.drawString(x, y, self.org)
        
        c.setFont("Helvetica-Bold", s - 1.5)
        c.setFillColor(INK)
        c.drawRightString(self.aw, y, self.dates)

class ProjectLine(Flowable):
    """Project title (clickable) ............ tech tags."""
    def __init__(self, title, tags, url=None, size=11):
        super().__init__()
        self.title, self.tags, self.url, self.size = title, tags, url, size

    def wrap(self, aw, ah):
        self.aw = aw
        return aw, self.size + 3

    def draw(self):
        c, s, y = self.canv, self.size, 3.0
        c.setFont("Helvetica-Bold", s)
        c.setFillColor(INK)
        c.drawString(0, y, self.title)
        
        if self.url:
            tw = stringWidth(self.title, "Helvetica-Bold", s)
            c.linkURL(self.url, (0, 0, tw, s + 2), relative=1, thickness=0)
            c.setStrokeColor(HexColor("#93C5FD"))
            c.setLineWidth(0.5)
            c.line(0, y - 1, tw, y - 1)
            
        c.setFont("Helvetica-BoldOblique", s - 1.5)
        c.setFillColor(MUTED)
        c.drawRightString(self.aw, y, self.tags)

def link(url, label):
    return f'<a href="{url}" color="{ACCENT_HEX}">{label}</a>'

SEP = '&nbsp;&nbsp;<font color="#94A3B8">•</font>&nbsp;&nbsp;'
def bullets(items):
    return [Paragraph(t, S["bullet"], bulletText="•") for t in items]

# ---------- content ----------
GH = "https://github.com/mirzaasadijaz"
story = []

# Header (Text left, Image right)
header_left = [
    Paragraph("Asad Ijaz", S["name"]),
    Paragraph("Data Scientist | AI &amp; Automation Developer", S["headline"]),
    Spacer(1, 4),
    Paragraph(link("mailto:mirzaasadijaz@gmail.com", "mirzaasadijaz@gmail.com") + SEP +
              "Faisalabad, Punjab, Pakistan" + SEP +
              link("https://www.asadijaz.xyz/", "asadijaz.xyz"), S["contact"]),
    Paragraph(link("https://www.linkedin.com/in/asad-ijaz-data-scientist/", "linkedin.com/in/asad-ijaz-data-scientist") + SEP +
              link(GH, "github.com/mirzaasadijaz") + SEP +
              link("https://hub.docker.com/u/mirzaasadijaz", "hub.docker.com/u/mirzaasadijaz"), S["contact"]),
]

if os.path.exists(IMG_PATH):
    # Professional 75x75 px square profile image layout
    img_size = 75
    profile_img = RLImage(IMG_PATH, width=img_size, height=img_size)
    
    header_table = Table(
        [[header_left, profile_img]], 
        colWidths=[FW - (img_size + 10), img_size + 10]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
else:
    # Fallback to standard layout if image is missing
    story.extend(header_left)

# Summary
story += [Spacer(1, SEC_GAP), Section("Summary"), Spacer(1, 4)]
story.append(Paragraph(
    "Data Scientist and AI &amp; automation developer who takes problems from raw data to working software: "
    "cleaning and modeling data, then shipping models and LLM agents inside apps and pipelines. Builds predictive "
    "models, deep learning networks and agentic RAG systems with LangGraph, and has published four containerized "
    "AI apps on Docker Hub (288 combined pulls). Python-first, on a software engineering base of SQL, Laravel, "
    "C++ and C#.", S["body"]))

# Skills
story += [Spacer(1, SEC_GAP), Section("Technical Skills"), Spacer(1, 4)]
skills = [
    ("Languages", "Python, SQL, PHP, C++, C#, .NET"),
    ("Machine Learning", "scikit-learn, TensorFlow, Keras, PyTorch, Keras Tuner, MLflow, CNNs, LSTMs, transfer learning, "
                         "predictive modeling, churn prediction, recommendation systems"),
    ("Data Analysis", "Pandas, NumPy, SciPy, Matplotlib, Plotly, exploratory data analysis, SQL"),
    ("LLM &amp; Agentic AI", "LangGraph, agentic RAG, hybrid search (dense + BM25), reranking, FAISS, multi-agent workflows, "
                          "tool calling, Gemini, Groq, Streamlit"),
    ("Backend &amp; Tools", "Laravel, Flask, MySQL, SQLite, Docker, Selenium, Git, GitHub"),
]
for k, v in skills:
    story.append(Paragraph(f"<b>{k}:</b> {v}", S["skill"]))

# Experience
story += [Spacer(1, SEC_GAP), Section("Experience"), Spacer(1, 4)]
story.append(RoleLine("Data Scientist", "Optimum Tech, Punjab, Pakistan", "Jul 2026 \u2013 Present"))
story += bullets([
    "Build and evaluate machine learning models in Python for predictive analytics, owning the work from data "
    "preparation through modeling to evaluation.",
    "Clean, explore and analyze datasets with Pandas, NumPy and SQL to produce reliable model inputs and clear findings.",
    "Present results with Matplotlib and Plotly visualizations that stakeholders can act on.",
])
story.append(Spacer(1, ITEM_GAP))
story.append(RoleLine("Freelance AI &amp; Backend Developer".replace("&amp;", "&"), "Self-Employed, Remote", "Feb 2026 \u2013 Present"))
story += bullets([
    "Design and build LLM agents and agentic RAG chatbots with LangGraph, Groq and Gemini, covering retrieval, "
    "tool calling and self-correction, delivered through Streamlit or web front ends.",
    "Automate manual workflows in Python: personalized bulk email, social media publishing and Selenium browser bots.",
    "Develop backend services and web applications with Laravel, Flask and MySQL.",
    "Containerize and ship applications with Docker; four AI apps published on Docker Hub (288 combined pulls).",
])
story.append(Spacer(1, ITEM_GAP))
story.append(RoleLine("Laravel Developer", "Optimum Tech, Punjab, Pakistan", "Jan 2024 \u2013 Dec 2025"))
story += bullets([
    "Built and maintained backend and frontend features for Laravel web applications.",
    "Worked with MySQL and SQL databases that powered application features.",
])

# Projects
story += [Spacer(1, SEC_GAP), Section("Projects"), Spacer(1, 4)]
projects = [
    ("Agentic RAG with Hybrid Search and Reranking", "LangGraph \u00b7 BM25 \u00b7 Cross-encoder \u00b7 Docker",
     GH + "/Agentic-RAG-with-LangGraph-Hybrid-Search-Reranking",
     "Agent that routes each question, retrieves with dense plus BM25 hybrid search, reranks with a cross-encoder, "
     "grades what it found and self-corrects weak answers. Published as a Docker image (149 pulls)."),
    ("JARVIS Personal AI Assistant", "LangGraph \u00b7 RAG \u00b7 Voice (Urdu + English)",
     GH + "/JARVIS",
     "Voice assistant locked behind a wake word and PIN, with a LangGraph agent orchestrating 35 tools (scheduling, "
     "email, research, maps, browser automation, file editing) and RAG over WhatsApp and local files."),
    ("Aura Accessories Shopping Assistant", "LangGraph \u00b7 Groq \u00b7 RAG",
     GH + "/Aura-Accessories-Agentic-RAG-Chatbot",
     "Agentic RAG chatbot for a luxury fashion brand: a ReAct agent on Groq decides when to search product data "
     "and when to answer directly."),
    ("Autonomous LinkedIn Publisher", "LangGraph \u00b7 Multi-agent \u00b7 Docker",
     GH + "/Autonomous-LinkedIn-AI-Publisher",
     "Multi-agent pipeline that finds a trending data science topic, researches it, writes the post, fact-checks it "
     "and publishes it to LinkedIn. Docker image: 48 pulls."),
    ("AI Email Dispatcher", "LangGraph \u00b7 Gemini \u00b7 Streamlit \u00b7 Docker",
     GH + "/AI-Agent-Email-Dispatcher",
     "Streamlit app where a Gemini-powered LangGraph workflow writes, themes, illustrates and sends personalized "
     "bulk email. Docker image: 46 pulls."),
    ("Deep Learning Projects", "TensorFlow \u00b7 Keras \u00b7 MobileNetV2",
     GH + "?tab=repositories",
     "ANN for California housing prices tuned with Keras Tuner (Hyperband) and benchmarked against classical baselines; "
     "CNNs for CIFAR-10 and MNIST with augmentation, batch normalization, dropout, L2, label smoothing and AdamW; "
     "MobileNetV2 transfer learning; LSTM next-word predictor trained on Kafka\u2019s The Metamorphosis."),
]
for i, (t, tags, url, d) in enumerate(projects):
    story.append(ProjectLine(t, tags, url))
    story.append(Paragraph(d, S["desc"]))
    if i != len(projects) - 1:
        story.append(Spacer(1, ITEM_GAP))

# Education
story += [Spacer(1, SEC_GAP), Section("Education"), Spacer(1, 4)]
story.append(RoleLine("BS Computer Science", "University of Agriculture, Faisalabad, Pakistan", "Sep 2024 \u2013 Aug 2028 (Expected)"))

# Internships & Certifications
story += [Spacer(1, SEC_GAP), Section("Internships & Certifications"), Spacer(1, 4)]
intern_certs = [
    "AI Engineer Internship From Optimum Tech",
    "Backend Development Internship",
    "The Ultimate Job Ready Data Science Course",
    "Data, Data, Everywhere",
]
LIST_SEP = f'&nbsp;&nbsp;<font color="{ACCENT_HEX}"><b>•</b></font>&nbsp;&nbsp;'
story.append(Paragraph(LIST_SEP.join(intern_certs), S["body"]))

# ---------- build ----------
def on_page(c, doc):
    c.saveState()
    c.setFillColor(ACCENT)
    c.rect(0, H - 8, W, 8, stroke=0, fill=1)
    c.restoreState()

doc = BaseDocTemplate(
    OUT, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
    title="Asad Ijaz - Data Scientist Resume", author="Asad Ijaz",
    subject="Resume: Data Scientist | AI & Automation Developer"
)
frame = Frame(LM, BM, FW, H - TM - BM, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="main")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
doc.build(story)
print("built", OUT)