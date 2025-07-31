import streamlit as st
import json
import ast
import os
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess

st.set_page_config(layout="wide", page_title="Multi File Analyzer")
st.title("🧠 Smart File Analyzer")
st.markdown("""
This Streamlit-based tool allows users to upload and analyze various file types—Python, JSON, CSV, and XML. 
It generates semantic models, summaries, and UML diagrams using LLM and PlantUML.
""")


tab1, tab2, tab3, tab4 = st.tabs(["🐍 Python", "📄 JSON", "🧾 CSV", "🧬 XML"])

# --------------------- PYTHON TAB -------------------------
with tab1:
    uploaded_file = st.file_uploader("Upload a Python file", type=[".py"])

    if uploaded_file is not None:
        st.subheader("📄 Uploaded Python Code")
        code = uploaded_file.read().decode("utf-8")
        st.code(code, language="python")

        class SemanticModelVisitor(ast.NodeVisitor):
            def __init__(self):
                self.model = {"functions": [], "classes": []}

            def visit_FunctionDef(self, node):
                self.model["functions"].append({"name": node.name, "args": [arg.arg for arg in node.args.args]})
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                self.model["classes"].append({"name": node.name, "methods": methods})
                self.generic_visit(node)

        tree = ast.parse(code)
        visitor = SemanticModelVisitor()
        visitor.visit(tree)
        semantic_model = visitor.model

        st.subheader("📘 JSON Semantic Model")
        st.json(semantic_model)

        st.subheader("📝 Summary")
        summary = f"This file contains {len(semantic_model['functions'])} functions and {len(semantic_model['classes'])} classes."
        st.write(summary)

        st.subheader("📌 Generate UML Diagram")

        def generate_uml_code(model: dict) -> str:
            lines = ["@startuml"]
            for cls in model["classes"]:
                lines.append(f"class {cls['name']} {{")
                for method in cls["methods"]:
                    lines.append(f"  {method}()")
                lines.append("}")
            for func in model["functions"]:
                lines.append(f"class {func['name']} {{")
                lines.append("  (function)")
                lines.append("}")
            lines.append("@enduml")
            return "\n".join(lines)

        uml_code = generate_uml_code(semantic_model)
        with open("diagram.puml", "w") as f:
            f.write(uml_code)

        if Path("plantuml.jar").exists():
            try:
                subprocess.run(["java", "-jar", "plantuml.jar", "diagram.puml"], check=True)
                st.image("diagram.png", caption="Generated UML Diagram")

                if os.path.exists("diagram.png"):
                  with open("diagram.png", "rb") as f:
                   st.download_button("⬇️ Download UML Diagram", f, file_name="uml_diagram.png")

            except subprocess.CalledProcessError:
                st.error("❌ Failed to generate UML diagram using PlantUML.")
        else:
            st.warning("⚠️ plantuml.jar not found in the current directory. Please place it here to generate UML diagrams.")
# --------------------- JSON TAB -------------------------
with tab2:
    uploaded_json = st.file_uploader("Upload a JSON file", type=["json"])
    if uploaded_json:
        try:
            json_data = json.load(uploaded_json)
            st.subheader("📄 JSON Viewer")
            st.json(json_data)

            st.subheader("📊 JSON UML Diagram")
            def json_to_puml(data, indent=0):
                puml = ""
                if isinstance(data, dict):
                    for key, value in data.items():
                        puml += " " * indent + f"class {key} {{\n"
                        if isinstance(value, dict) or isinstance(value, list):
                            puml += json_to_puml(value, indent + 2)
                        puml += " " * indent + "}\n"
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        puml += json_to_puml(item, indent)
                return puml

            puml_json = "@startuml\n" + json_to_puml(json_data) + "@enduml"
            with open("diagram.puml", "w") as f:
                f.write(puml_json)

            subprocess.run(["java", "-jar", "plantuml.jar", "diagram.puml"], check=True)
            st.image("diagram.png")
            if os.path.exists("diagram.png"):
              with open("diagram.png", "rb") as f:
                st.download_button("⬇️ Download UML Diagram", f, file_name="uml_diagram.png")


        except Exception as e:
            st.error(f"JSON Processing Error: {e}")

# --------------------- CSV TAB -------------------------
with tab3:
    uploaded_csv = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_csv:
        try:
            df = pd.read_csv(uploaded_csv)
            st.subheader("📋 CSV Table")
            st.dataframe(df)

            st.subheader("📈 Summary")
            st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
            st.write(f"Columns: {list(df.columns)}")
            st.write("🧮 Basic Stats:")
            st.write(df.describe(include='all'))
        except Exception as e:
            st.error(f"CSV Reading Error: {e}")

# --------------------- XML TAB -------------------------
with tab4:
    uploaded_xml = st.file_uploader("Upload an XML file", type=["xml"])
    if uploaded_xml:
        try:
            tree = ET.parse(uploaded_xml)
            root = tree.getroot()

            def print_xml(elem, level=0):
                indent = " " * (level * 2)
                out = f"{indent}<{elem.tag}>"
                for child in elem:
                    out += "\n" + print_xml(child, level + 1)
                if list(elem):
                    out += f"\n{indent}</{elem.tag}>"
                else:
                    out += f"{elem.text}</{elem.tag}>"
                return out

            st.subheader("🔍 XML Content")
            st.text(print_xml(root))
        except Exception as e:
            st.error(f"XML Parsing Error: {e}")

