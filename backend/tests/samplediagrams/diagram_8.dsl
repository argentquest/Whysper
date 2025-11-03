workspace {
      model {
        patient = person "Patient"
        healthSystem = softwareSystem "Health Record System" {
          portal = container "Patient Portal"
          service = container "Health Service"
          db = container "Health Database"
          patient -> portal "Views records"
          portal -> service "Requests data"
          service -> db "Reads and writes"
        }
      }
      views {
        container healthSystem {
          include *
          autolayout lr
        }
      }
    }