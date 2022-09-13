extra_column = {
    'WageSystemKey': 'Employee ID as seen in the Interface',
    'StartDate': 'Employee Starting Date',
    'EndDate': 'Employee Ending Date',
    'WageModel': 'Contract Type',
    'FirstName': 'Actually just the name of the employee',
    'DepartmentKey': 'Store ID as seen in Department List',
    'DepartmentStartDate': 'Date at which employee starts at this department'
}

string_example = "Paste the JSON object that you received in here\nLine Breaks can or cannot be put in \n \nExample: \n \n{\n\t'Employees':  [\n\t\t{\n\t\t'WageSystemKey': '001',\n\t\t'DepartmentKey':'DEP-1',\n\t\t'WageModel':'Monthly Wage',\n\t\t'FirstName':'Jane Doe'\n\t\t}\n\t],\n\t'ImportSettings':\n\t\t{\n\t\t'ShouldActivateEmployee':true,\n\t\t'ForceUpdateEmployeeHistories':true,\n\t\t'ContractTypeStartDateEqualsEmployeeStartDate':true,\n\t\t'HomeDepartmentStartDateEqualsEmployeeStartDate':true,\n\t\t'PositionStartDateEqualsEmployeeStartDate':true,\n\t\t'ShouldUpdateEmptyValuesOnFields':true,\n\t\t'ShouldSendActivationEmail':true,'MovePreviousEntry':true\n\t\t}\n}"