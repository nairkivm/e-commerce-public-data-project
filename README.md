# E-Commerce Public Data Project

## How to run the dashboard on local

1. Copy this repository on your machine. This code is written in python and Ipython, so your machine should have been installed with Python (>=3.11), Jupyter Notebook, virtual environment (venv), and package manager like pip.
2. Go to the directory of this project on your machine and create a virtual environment by running `python -m venv <name-of-your-ve>` in your terminal.
3. Activate the virtual environment by running `<name-of-your-ve>\Scripts\activate.bat` if you're using Windows or `source <name-of-your-ve>/bin/activate` if you're using MacOS or Linux.
4. Install the dependencies by running `pip install -r requirements.txt`.
5. Now, you can run the notebook and activate the dashboard. You can start the dashboard app service by running `python -m streamlit run streamlit_app.py`. After you run this, you will be redirected (or if it's not automatic, you can go to) to your web browser in `localhost:8501`.
6. Explore the dashboard! You can do general filtering by modifying the filters in the sidebar. There are *Date*, *Order status*, *Product category*, *City*, and *State* filters.
7. There are three section on this dashboard: *Overview*, *Product Portofolio*, *Demographic Analysis*. The Overview contains general metrics about the current main situation on the business, the Product Portofolio contains more detailed metrics about the products's performance and it's relation with review score, and Demographic Analysis contains more detailed metrics about the customers. You can also switch the map settings by choosing your preferred aggregate variable and value.

## How to run the dashboard without local installation

You can go to this [link](https://nairkivm-e-commerce-public-data-project-streamlit-app-gwhjnq.streamlit.app/) to explore the dashboard with less effort!