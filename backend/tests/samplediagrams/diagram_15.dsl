workspace {
      model {
        user = person "User 5"
        system = softwareSystem "System 5" {
          frontend = container "Frontend 5"
          backend = container "Backend 5"
          db = container "Database 5"
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