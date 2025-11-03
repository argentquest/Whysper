workspace {
      model {
        reader = person "Reader"
        librarySystem = softwareSystem "Digital Library" {
          app = container "Library App"
          api = container "Library API"
          catalog = container "Book Catalog"
          reader -> app "Searches books"
          app -> api "Requests"
          api -> catalog "Fetches info"
        }
      }
      views {
        container librarySystem {
          include *
          autolayout lr
        }
      }
    }