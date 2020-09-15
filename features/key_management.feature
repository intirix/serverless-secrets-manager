Feature: Users can manage their keys
/v1/users/{username}/keys/private/encrypted

    Scenario: A user can get their encrypted private key
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And "myuser" will log in with password "password"
        And path parameter "username" is set to "myuser"
        When I "GET" "/v1/users/{username}/keys/private/encrypted"
        Then I get a "200" response code
        And I get response header "Content-Type" of "application/octet-stream"