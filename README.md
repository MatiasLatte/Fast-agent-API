# Nassau National Cable Chatbot

A FastAPI based intelligent assistant that helps customers with technical information about our cable products. This system combines our Shopify catalog to provide product specifications, installation guidance, and usage recommendations.

## What it does

The AI assistant handles customer inquiries about cable products, focusing on technical specifications rather than sales. It can help with:  
- Product specifications and technical details  
- Installation guidelines and best practices  
- Cable compatibility and application advice  
- Safety standards and certifications  
- Material properties and environmental ratings  

The assistant is designed to be informative only. It won't discuss pricing, inventory, or sales topics.

## Technical setup

Built with FastAPI and FastAgent, this service connects to our Shopify product database through the Shopify MCP server. The AI uses Claude 3.5 Haiku to understand customer questions and provide relevant technical information.

## Requirements

- Python 3.12+  
- Valid Shopify API credentials  
- Anthropic API key  
- Node.js (for the MCP server)  

## Configuration

The system uses two configuration approaches due to compatibility issues:  

### fastagent.secrets.yaml :
```yaml
anthropic:
  api_key: "your_anthropic_key"
````

### Environment variables:

```env
SHOPIFY_ACCESS_TOKEN=your_shopify_token
MYSHOPIFY_DOMAIN=your-store.myshopify.com  
```

Note: There's some redundancy between these files, but for optimal support setup both methods with this setup.

## Running locally

Install dependencies:

```bash
pip install -r requirements.txt
npm install -g shopify-mcp
```

Set up your environment variables (create a .env file or export them)

```bash
export SHOPIFY_ACCESS_TOKEN= “your_shopify_token”
export SHOPIFY_DOMAIN= “your-store.myshopify.com”
```

Configure fastagent.secrets.yaml with your API keys (see configuration section above)

Start the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at [http://localhost:8000](http://localhost:8000)

## EC2 Deployment

### Launch EC2 Instance:

* Amazon Linux 2 AMI
* t3.medium (recommended minimum)
* Security group: Allow port 8000

### Install Docker on Ec2:

```bash
sudo yum update -y 
sudo yum install -y docker 
sudo systemctl start docker 
sudo usermod -a -G docker ec2-user
```

### Upload Project Files:

```bash
scp -r * ec2-user@your-ec2-ip:/home/ec2-user/fast-agent-api/
```

### Deploy on EC2:

```bash
ssh ec2-user@your-ec2-ip 

cd fast-agent-api 

# Set up environment variables
nano .env  # Add your API keys 

# Deploy 
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify deployment:

```bash
curl http://your-ec2-ip:8000/health
```

## API endpoints

* GET / - Basic status check
* GET /health - Health check
* POST /chat - Send messages to the AI assistant

### Example chat request:

```json
{
  "message": "What cable should I use for outdoor installation?"
}
```

## Deployment notes

This is designed to run on EC2. Make sure to:

* Configure environment variables on the server
* Open port 8000 in security groups

## Project structure

The main application logic is in main.py. Configuration for FastAgent is split between fastagent.config.yaml (MCP server setup) and fastagent.secrets.yaml (API keys).

## Credits

* FastAgent - [Agent framework](https://github.com/evalstate/fast-agent)
* Shopify MCP Server - [Shopify integration](https://github.com/asaricorp/mcp-shopify)
* Anthropic Claude - [AI language model](https://claude.ai/)

Built for Nassau National Cable's customer support team
