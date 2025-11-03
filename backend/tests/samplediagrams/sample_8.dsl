workspace {
  model {
    patient = person "Patient"
    healthSystem = softwareSystem "Healthcare System" {
      app = container "Mobile App"
      server = container "Backend Server"
      records = container "Medical Records DB"
      patient -> app "Uses"
      app -> server "Communicates"
      server -> records "Accesses records"
    }
  }
  views {
    container healthSystem {
      include *
      autolayout lr
    }
  }
}