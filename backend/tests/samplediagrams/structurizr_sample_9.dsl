workspace {
  model {
    manager = person "Manager"
    hr = softwareSystem "HR System" {
      portal = container "Portal"
      db = container "Employee DB"
      manager -> portal "Manages employees"
      portal -> db "Reads/Writes"
    }
  }
  views {
    container hr {
      include *
      autolayout lr
    }
  }
}