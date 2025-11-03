workspace {
  model {
    patient = person "Patient"
    healthSystem = softwareSystem "Healthcare System" {
      container app "Mobile App"
      container server "Backend Server"
      container records "Medical Records DB"
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