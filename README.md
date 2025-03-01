# Online-Commerce
An e-commerce website with product browsing, shopping cart, and user registration functionality. 

Names and Roles of Team Members
- Shameer Ahmad (Development Engineer - Login and Session)
- Anthony Yang (Development Engineer - Login and Searching)
- Katherine Kelly (Development Engineer - Cart)
- Madie Simmons (Development Engineer - Cart)
- Joseph Kim (Test Engineer -)

# Create a virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


# Run the app
flask run

# Running tests
cd tests
export PYTHONPATH=$(pwd)/..
pytest