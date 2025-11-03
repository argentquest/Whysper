workspace {
  model {
    student = person "Student"
    lms = softwareSystem "Learning Management System" {
      ui = container "UI"
      backend = container "Backend"
      student -> ui "Accesses courses"
      ui -> backend "Requests"
    }
  }
  views {
    container lms {
      include *
      autolayout lr
    }
  }
}