Feature: Adunit

Scenario: query the positions belong to the same medium of the unit
    Given there is a medium called test_medium
    And there is a position called test_position and a unit called test_unit. They belong to the medium
    When there is one more position
    Then the count of positions belong to the same medium with the position should be 1