import streamlit as st
import openai
import subprocess
import json
import os
import pandas as pd

# Paths
terraform_dir = "uploaded_files"
generated_file_path = os.path.join(terraform_dir, "main.tf")

# Ensure working directory exists
os.makedirs(terraform_dir, exist_ok=True)

# OpenAI Key Setup
openai.api_key = "OPEN-APi-KEY"

# Function to generate Terraform code from a prompt
def clean_terraform_code(code):
    # Remove Markdown formatting (```hcl and ```)
    if code.startswith("```hcl"):
        code = code[6:]  # Remove the opening ```hcl
    if code.endswith("```"):
        code = code[:-3]  # Remove the closing ```
    return code.strip()

def generate_terraform_code(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that generates Terraform code."},
                {"role": "user", "content": prompt},
            ],
        )
        terraform_code = response["choices"][0]["message"]["content"].strip()
        return clean_terraform_code(terraform_code)
    except Exception as e:
        st.error(f"Error generating Terraform code: {e}")
        return ""


# Function to run terraform commands
def run_terraform_command(command, description):
    try:
        result = subprocess.run(
            command,
            cwd=terraform_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            st.success(f"{description} executed successfully!")
            st.text(result.stdout)
            return True
        else:
            st.error(f"{description} failed!")
            st.text(result.stderr)
            return False
    except Exception as e:
        st.error(f"Error during {description}: {e}")
        return False

# Function to parse the Terraform state file
def parse_terraform_state():
    state_file_path = os.path.join(terraform_dir, "terraform.tfstate")
    if not os.path.exists(state_file_path):
        st.warning("Terraform state file not found!")
        return []

    with open(state_file_path, "r") as f:
        state_data = json.load(f)

    resources = []
    for resource in state_data["resources"]:
        for instance in resource.get("instances", []):
            attributes = instance.get("attributes", {})
            resources.append({
                "Resource Type": resource["type"],
                "Name": resource["name"],
                "ID": attributes.get("id", "N/A"),
                "CIDR Block": attributes.get("cidr_block", "N/A")
            })
    return resources

# Streamlit UI
st.title("Terraform Resource Explorer")
st.write("Generate Terraform files by prompt or upload an existing file, validate, plan, and apply.")

# Step 1: Generate or Upload Terraform File
st.header("Step 1: Generate or Upload Terraform File")

# Option to generate Terraform file
tab1, tab2 = st.tabs(["Generate Terraform File", "Upload Terraform File"])

with tab1:
    st.subheader("Generate Terraform File by Prompt")
    user_prompt = st.text_area("Describe your infrastructure", placeholder="E.g., Create a VPC with two subnets...")
    if st.button("Generate Terraform File"):
        if user_prompt:
            terraform_code = generate_terraform_code(user_prompt)
            if terraform_code:
                with open(generated_file_path, "w") as tf_file:
                    tf_file.write(terraform_code)
                st.success("Terraform file generated successfully!")
                st.code(terraform_code, language="hcl")
        else:
            st.error("Please provide a prompt to generate Terraform code.")

with tab2:
    st.subheader("Upload Terraform File")
    uploaded_file = st.file_uploader("Choose a Terraform file", type=["tf"])
    if uploaded_file:
        with open(generated_file_path, "wb") as tf_file:
            tf_file.write(uploaded_file.getbuffer())
        st.success(f"File uploaded: {uploaded_file.name}")

# Step 2: Terraform Commands
# Step 2: Terraform Operations
if os.path.exists(generated_file_path):
    st.header("Step 2: Terraform Operations")

    # Initialize Terraform
    if st.button("Initialize Terraform"):
        run_terraform_command(["terraform", "init"], "Terraform Init")
    
    # Validate
    if st.button("Validate Terraform File"):
        run_terraform_command(["terraform", "validate"], "Terraform Validate")
    
    # Plan
    if st.button("Generate Terraform Plan"):
        run_terraform_command(["terraform", "plan"], "Terraform Plan")
    
    # Apply
    if st.button("Run Terraform Apply"):
        run_terraform_command(["terraform", "apply", "-auto-approve"], "Terraform Apply")
    
    # Optional: Force Unlock State
    with st.expander("Resolve State Lock Issues"):
        st.write("If you encounter state lock issues, you can force unlock the state.")
        lock_id = st.text_input("Enter Lock ID (from error message)")
        if st.button("Force Unlock State"):
            if lock_id:
                run_terraform_command(["terraform", "force-unlock", "-force", lock_id], "Force Unlock State")
            else:
                st.warning("Please provide a valid Lock ID.")
    
    # Display resources
    st.header("Created Resources")
    resources = parse_terraform_state()
    if resources:
        st.table(pd.DataFrame(resources))
    else:
        st.info("No resources found. Run Terraform Apply to create resources.")
