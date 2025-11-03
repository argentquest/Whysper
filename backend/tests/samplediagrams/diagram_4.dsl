workspace {
      model {
        employee = person "Employee"
        hrSystem = softwareSystem "HR System" {
          portal = container "Employee Portal"
          service = container "HR Service"
          db = container "HR Database"
          employee -> portal "Accesses HR info"
          portal -> service "Requests data"
          service -> db "Reads and writes"
        }
      }
      views {
        container hrSystem {
          include *
          autolayout lr
        }
      }
    }