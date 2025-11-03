workspace {
      model {
        user = person "User 7"
        system = softwareSystem "System 7" {
          frontend = container "Frontend 7"
          backend = container "Backend 7"
          db = container "Database 7"
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