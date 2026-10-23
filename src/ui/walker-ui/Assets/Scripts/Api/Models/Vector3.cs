namespace Api.Models {
    // Vector exchanged with the API.
    // 
    // It converts implicitly from and to UnityEngine.Vector3.
    public class Vector3 : ApiModel<Vector3> {
        public float x;
        public float y;
        public float z;

        public static implicit operator Vector3(UnityEngine.Vector3 vector) {
            return new Vector3 { x = vector.x, y = vector.y, z = vector.z };
        }

        public static implicit operator UnityEngine.Vector3(Vector3 vector) {
            return new UnityEngine.Vector3(vector.x, vector.y, vector.z);
        }
    }
}
