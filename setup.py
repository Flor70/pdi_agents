from setuptools import setup, find_packages

setup(
    name="pdi_crew",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'crewai',
        'langchain-openai',
        'pydantic',
        'python-dotenv',
        'exa-py'
    ]
)
