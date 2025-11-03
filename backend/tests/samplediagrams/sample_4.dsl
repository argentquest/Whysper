workspace {
  model {
    employee = person "Employee"
    hrSystem = softwareSystem "HR System" {
      portal = container "Employee Portal"
      db = container "HR Database"
      employee -> portal "Accesses"
      portal -> db "Queries"
    }
  }
  views {
    container hrSystem {
      include *
      autolayout lr
    }
  }
}