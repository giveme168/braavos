Feature: Adposition

Scenario: query the units from a position
    Given there is a medium called test_medium
    And there is a position called test_position and a unit called test_unit. They belong to the medium
    When there is one more unit
    Then the count of units belong to the same medium with the position is 1