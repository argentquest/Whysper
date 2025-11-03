workspace {
  model {
    student = person "Student"
    lms = softwareSystem "Learning Management System" {
      ui = container "User Interface"
      service = container "Service Layer"
      repo = container "Content Repository"
      student -> ui "Uses"
      ui -> service "Invokes"
      service -> repo "Fetches content"
    }
  }
  views {
    container lms {
      include *
      autolayout lr
    }
  }
}