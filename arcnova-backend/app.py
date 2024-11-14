import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from diagrams import Diagram
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import Route53
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import S3
import spacy
import base64
import logging
from huggingface_hub import InferenceClient

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Ensure 'static' directory exists for diagrams
if not os.path.exists("static"):
    os.makedirs("static")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS service nodes mapping
SERVICE_NODES = {
    "ec2": EC2,
    "lambda": Lambda,
    "rds": RDS,
    "dns": Route53,
    "monitoring": Cloudwatch,
    "s3": S3,
}

# Initialize the Hugging Face Inference Client
client = InferenceClient(api_key="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")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_steps_with_phi3(user_input):
    """Generate step-by-step instructions using Hugging Face InferenceClient."""
    try:
        logger.info("Generating steps using Phi-3.5-mini-instruct model...")
        # Prepare the conversation for the model
        messages = [
            {"role": "system", "content": "You are an AWS consultant"},
            {
                "role": "user",
                "content": f"Provide step-by-step instructions for {user_input}. Keep the instructions easy and concise."
            },
        ]

        # Stream the response from the Hugging Face API
        stream = client.chat.completions.create(
            model="microsoft/Phi-3.5-mini-instruct",
            messages=messages,
            max_tokens=500,
            stream=True
        )
        
        # Collect and return the output text
        steps = ''.join(chunk.choices[0].delta.content for chunk in stream)
        logger.info("Steps generated successfully.")
        return steps

    except Exception as e:
        logger.error(f"Error generating steps: {e}")
        raise

def extract_services(steps):
    """Extract AWS services mentioned in the steps using NLP."""
    logger.info("Extracting services from the generated steps...")
    doc = nlp(steps.lower())
    services = set()

    for token in doc:
        if token.text in SERVICE_NODES:
            services.add(token.text)

    logger.info(f"Extracted services: {services}")
    return list(services)

def generate_dynamic_diagram(services, layout="TB"):
    """Generate an AWS architecture diagram based on extracted services."""
    logger.info(f"Generating architecture diagram with layout: {layout}...")
    with Diagram("Dynamic AWS Architecture", show=False, filename="static/dynamic_diagram", direction=layout):
        nodes = []
        for service in services:
            if service in SERVICE_NODES:
                nodes.append(SERVICE_NODES[service](service.upper()))
            else:
                logger.warning(f"Service {service} not recognized in SERVICE_NODES mapping")

        for i in range(len(nodes) - 1):
            nodes[i] >> nodes[i + 1]

@app.post("/generate-diagram-and-steps")
async def generate_diagram_and_steps(request: Request):
    start_time = time.time()  # Start timer to track total processing time

    data = await request.json()
    user_input = data.get("input", "")
    layout = data.get("layout", "TB")  # Default layout is "TB" (top to bottom)

    logger.info(f"Received user input: {user_input}")

    # Generate step-by-step instructions using Hugging Face API
    steps = await generate_steps_with_phi3(user_input)

    # Extract services from the generated steps
    services = extract_services(steps)

    # Generate the architecture diagram
    generate_dynamic_diagram(services, layout=layout)

    # Encode the diagram in Base64
    with open("static/dynamic_diagram.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    end_time = time.time()  # End timer to calculate total processing time
    processing_time = end_time - start_time
    logger.info(f"Total processing time: {processing_time:.2f} seconds.")

    # Return both the diagram and the generated steps
    return {"diagram": encoded_string, "steps": steps}
