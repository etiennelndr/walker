namespace Api.Models {
    public class Ray : ApiModel<Ray> {
        public Vector3 origin;
        public Vector3 direction;
    }


    public class RayCollision : ApiModel<RayCollision> {
        public Ray ray;
        public Vector3 point;
    }
}
