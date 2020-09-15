Feature: Users can be added

    Scenario: Users can be created
        Given I have installed the system
        And "admin" will log in with password "password"
        And path parameter "username" is set to "myuser"
        And POST body field "displayName" is set to "My User"
        When I "POST" "/v1/users/{username}"
        Then I get a "201" response code

    Scenario: An admin can create a new keypair for a user
        Given I have installed the system
        And user "myuser" exists
        And "admin" will log in with password "password"
        And path parameter "username" is set to "myuser"
        And query string parameter "generate" is set to "true"
        And POST body is "password"
        When I "POST" "/v1/users/{username}/keys"
        Then I get a "200" response code
        And I get response header "Content-Type" of "application/x-pem-file"

    Scenario: The body must contain the password in order to generate a keypair
        Given I have installed the system
        And user "myuser" exists
        And "admin" will log in with password "password"
        And path parameter "username" is set to "myuser"
        And query string parameter "generate" is set to "true"
        When I "POST" "/v1/users/{username}/keys"
        Then I get a "400" response code
