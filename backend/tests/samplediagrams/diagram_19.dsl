workspace {
      model {
        user = person "User 9"
        system = softwareSystem "System 9" {
          frontend = container "Frontend 9"
          backend = container "Backend 9"
          db = container "Database 9"
          user -> frontend "Uses"
          frontend -> backend "Calls"
          backend -> db "Stores data"
        }
      }
      views {
        container system {
          include *
          autolayout lr
        }
      }
    }