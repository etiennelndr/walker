using System;
using System.Collections.Generic;

using UnityEngine;

namespace Api.Models {
    [Serializable]
    public class State : ApiModel<State> {
        public List<RayCollision> collisions;
        public Vector3 speed;
    }
}
