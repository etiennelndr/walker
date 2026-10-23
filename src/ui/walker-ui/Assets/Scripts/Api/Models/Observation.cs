using System.Collections.Generic;

namespace Api.Models {
    public class Observation : ApiModel<Observation> {
        public List<RayCollision> collisions;
        public Vector3 velocity;
    }
}
