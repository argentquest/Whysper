workspace {
  model {
    employee = person "Employee"
    hrSystem = softwareSystem "HR System" {
      container portal "Employee Portal"
      container db "HR Database"
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