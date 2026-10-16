using System;

using UnityEngine;

namespace Api.Models {
    [Serializable]
    public class Ray : ApiModel<Ray> {
        public Vector3 origin;
        public Vector3 direction;
    }


    [Serializable]
    public class RayCollision : ApiModel<RayCollision> {
        public Ray ray;
        public Vector3 point;
    }
}
