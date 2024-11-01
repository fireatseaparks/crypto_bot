# crypto_bot
The main goal of this project is to create a trading bot based on a Machine Learning model that will invest in crypto markets.

## Step 1 / Discovery of available data sources : Deadline mi-sprint 4
- Define the context and scope of the project (do not underestimate this step)
- Get to know the different data sources, the APIs and the web pages
- Expected deliverable : You will have to provide a report explaining the different data sources with examples of collected data

## Step 2 / Data organization : Deadline MC 5
- This will be the most important part of your project where you will be doing the core business of Data Engineer.
- You will be asked to organize the data via different databases:
  - Relational
  - NoSQL
- You will need to think about the data architecture, including how to link the different data together.
- Deliverable : Any document explaining the chosen architecture (UML diagram)

## Step 3 / Data consumption : Deadline MC 7
- Once your data is organized, it has to be consumed, this is not the initial role of a Data Engineer, but for the data pipeline to be complete, you need to have this part.
- It will be expected to make a notebook where you will do Machine Learning on it or a dashboard with Dash
- Expected Deliverable:
  - The notebook should be clean, accompanied by dataviz and commented. Code cells should be preceded by text cells.
  - Python file launching the Dash

## Step 4 / Deployment : Deadline mi-sprint 9
- Create an API of the Machine Learning model or Dash application
- Perform unit tests on your API
- Containerize this API via Docker and databases
- Orchestrate the different services via Kubernetes

## Step 5 / Flow automation (OPTIONAL) :
- Automate the various previous steps so that the application is continuously functional
- Set up a CI/CD pipeline to efficiently update your application

## Step 6 / Demonstration of the application + Support (30 minutes) : 20 - 22 of January
- Demonstrate the progress of your project
- Explain the architecture chosen when organizing the data
- Show that the application is functional
- It will not be expected to talk in detail about the data consumption section
