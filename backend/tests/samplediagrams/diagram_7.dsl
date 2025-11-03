workspace {
      model {
        visitor = person "Visitor"
        museumSystem = softwareSystem "Museum Guide System" {
          app = container "Mobile App"
          guideService = container "Guide Service"
          contentDB = container "Content Database"
          visitor -> app "Uses"
          app -> guideService "Requests info"
          guideService -> contentDB "Fetches content"
        }
      }
      views {
        container museumSystem {
          include *
          autolayout lr
        }
      }
    }