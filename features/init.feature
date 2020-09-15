Feature: The system can initialize itself when first invoked

    Scenario: Start the system
        Given I have installed the system
        And "admin" will log in with password "password"
        When I "GET" "/v1/users"
        Then I get a "200" response code