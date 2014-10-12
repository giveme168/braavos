Feature: Adposition

Scenario: query the units from a position
    Given there is a medium called test_medium
    And there is a position called and a unit. They belong to the medium and sizes are the same(200, 50)
    When there is two more units. One is in the same medium and default size
    And The other is in the same size with default medium
    Then the count of units belong to the same medium with the position is 1