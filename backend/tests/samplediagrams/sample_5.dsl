workspace {
  model {
    student = person "Student"
    lms = softwareSystem "Learning Management System" {
      container ui "User Interface"
      container service "Service Layer"
      container repo "Content Repository"
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