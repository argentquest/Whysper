workspace {
      model {
        student = person "Student"
        lms = softwareSystem "Learning Management System" {
          ui = container "User Interface"
          backend = container "Backend Service"
          repo = container "Course Repository"
          student -> ui "Uses"
          ui -> backend "Requests"
          backend -> repo "Fetches courses"
        }
      }
      views {
        container lms {
          include *
          autolayout lr
        }
      }
    }