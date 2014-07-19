Feature: Team

Scenario: use name, create team
    Given team名字: OneTeam
    When 创建对应名字的team
    Then 用这个名字的 1 个team被创建了.