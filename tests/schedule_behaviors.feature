Feature: Schedule

Scenario: add one unit to a position
    Given I have a position with one unit. And the estimate_num of the unit is 800
    When order an item with 600
    Then order successfully