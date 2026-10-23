namespace Api.Models {
    // Observation of a walker along with what is needed to train or evaluate the models with it.
    // Fields that do not apply to the behaviour of the walker are left empty and are not sent.
    public class Record : ApiModel<Record> {
        public string session;
        public string walker;
        public string scene;
        public int frame;
        public float time;
        public Observation observation;

        // Training fields
        public Vector3 desiredVelocity;
        public Vector3 target;

        // Patrolling fields
        public int? contacts;
        public Vector3 walk;
    }
}
