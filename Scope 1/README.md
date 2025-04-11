# **Introduction**

This project is a Django-based application that uses Docker for containerization and deployment. It includes:

1. A Django application.  
2. A `DockerFile` for building the Docker image.  
3. A `docker-compose.yml` file for managing multi-container deployments.

The goal is to simplify the deployment process, making it seamless and reproducible.

# **Getting Started**

Follow these steps to get the project up and running:

## **1\. Installation Process**

**Clone the repository**:  
git clone https://GS-SWDC@dev.azure.com/GS-SWDC/Data%20Team/\_git/Modern%20Arabert%20and%20Ticket%20Classification

1. cd django-app  
2. **Install Docker and Docker Compose**

## **2\. Software Dependencies**

Ensure the following are installed on your system:

* Docker (v20.10+)  
* Docker Compose (v2.0+)  
* Python (if running locally for development)

## **3\. Latest Releases**

Work is ongoing on the **ali\_sameh** branch.

## **Building the Docker Image**

1. Start the application using Docker Compose:  
   docker-compose up \--build  
   This will:  
   * Build the image if not already built.  
   * Start the Django app on `http://localhost:8000`.  
2. Access the application logs:  
   docker-compose logs \-f

## **Running Migrations**

After the application is up, run the following command to apply migrations:

docker-compose exec django-app python manage.py migrate

# **Contribute**

Contributions are welcome\! Follow these steps to contribute:

1. **Fork the repository**.  
2. **Clone your fork**:  
3. **Create a new branch**:  
4. **Make changes and commit**:  
5. **Push to your branch**:

