# Online-Commerce
An e-commerce website with product browsing, shopping cart, and user registration functionality. 

Names and Roles of Team Members
- Shameer Ahmad (Development Engineer - )
- Anthony Yang (Development Engineer - )
- Katherine Kelly (Development Engineer - Cart)
- Madie Simmons (Development Engineer - Cart)
- Joseph Kim (Test Engineer)


# Description of Tests and Approach to Testing

In our testing approach for the e-commerce website, we created a comprehensive test suite that validates the key functionality across different components of the application. Rather than following test-driven development (where tests would be written before the implementation), we implemented tests after the core functionality was developed.

## Testing Strategy

We employed pytest as our testing framework and focused on unit and integration testing of the application's core features:

### Authentication Testing
- **User Registration**: Tests that new users can register successfully, validates that required fields work as expected, and verifies duplicate username checks.
- **User Login**: Ensures the login page loads correctly and validates authentication logic.
- **User Logout**: Confirms the logout functionality clears the session and redirects appropriately.

### Shopping Cart Testing
- **Cart Session Management**: Validates that shopper IDs are created and stored in sessions correctly.
- **Adding Items**: Tests the ability to add products to the cart with specified quantities.
- **Retrieving Cart Contents**: Verifies that items added to the cart can be retrieved with correct properties.
- **Cart Calculations**: Tests the total price calculation functionality for cart items.
- **Cart Cleanup**: Validates that outdated items can be removed from the cart.

### Product Search Testing
- **Empty Search**: Tests behavior when no search query is provided.
- **Valid Search**: Verifies that products can be found when searching with relevant terms.
- **No Results**: Ensures appropriate handling when searches return no results.

### Category Browsing Testing
- **Category Display**: Tests that products in a specific category can be displayed correctly.
- **Invalid Category**: Verifies proper error handling when accessing non-existent categories.

### Integration Testing
- **End-to-End Shopping Flow**: Tests the entire shopping process from browsing to checkout, including product selection, cart management, and the login requirement for checkout.

## Test Implementation Approach

Our approach included:

1. **Isolated Testing Environment**: Created a separate testing database for each test run to ensure test isolation.
2. **Fixtures**: Used pytest fixtures for application context, test client, and helper functions.
3. **Test Data**: Programmatically inserted test data needed for each test scenario.
4. **Database Structure Simulation**: Created test versions of database tables and views to match production structure.
5. **Assertion Flexibility**: Made assertions somewhat flexible to accommodate small implementation changes.
6. **Error Detection**: Ensured tests would detect both functional issues and database schema problems.

## Challenges and Solutions

During test development, we encountered and solved several challenges:

1. **Database Views**: The application used specialized views like "Alphabetical list of products" from the Northwind database. We created equivalent tables in the test environment to simulate these views.
2. **Redirect Handling**: Made tests resilient to changes in redirect paths by checking for redirect behavior rather than specific URLs.
3. **Data Structure Adaptation**: Modified tests to be flexible about the structure of returned data from cart operations.

## Benefits of Our Testing Approach

1. **Maintainability**: Separate tests for each component make it easier to identify issues.
2. **Coverage**: Tests cover all major application features.
3. **Isolation**: Tests run independently without affecting each other.
4. **Documentation**: Tests serve as documentation of expected application behavior.
5. **Regression Detection**: Comprehensive test suite will catch issues if changes break existing functionality.

These tests help ensure the reliability of the e-commerce application and provide a safety net for future development.

Features of our solution we consider interesting:
- Customers can browse products via a categories drop-down, search, or just through the home page if they want to explore many different items/are not sure what they want to purchase
- Quantity alteration occurs in cart, whose page you are directed to after adding an item (as this will save time for the customer, for example if they are only purchasing one item or if they are not sure of quantities until everything is in their cart and want to change many quantities at once)
- The maximum quantity a customer can add to the cart is what is in stock according the the Northwind database 

