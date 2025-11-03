workspace {
      model {
        customer = person "Customer"
        bookingSystem = softwareSystem "Booking System" {
          mobileApp = container "Mobile App"
          api = container "API"
          db = container "Database"
          customer -> mobileApp "Books tickets"
          mobileApp -> api "Calls"
          api -> db "Stores booking info"
        }
      }
      views {
        container bookingSystem {
          include *
          autolayout lr
        }
      }
    }