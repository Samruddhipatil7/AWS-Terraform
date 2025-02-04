Terraform AWS Resource Provisioning

This project uses Terraform to automate the creation of AWS resources. You can dynamically generate Terraform configuration files based on your resource prompts.

Example: Creating a VPC
To create a VPC with a specific CIDR range, follow these steps:
Generate the Terraform File
Prompt the system with the following command:
Create a VPC with CIDR range 10.0.0.0/16
Click 
1. Terraforn init
2. Terraform plan
3. Terraform apply
After applying these steps, the AWS service (in this case, the VPC) will be created and can be viewed in the AWS Console. 

Add this in your code   

1. Add open-ai-gpt key
2. configure your aws cli in your terminal 
