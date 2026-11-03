using System.Collections.Generic;
using System.Linq;

using UnityEngine;

// Points between which training walkers move, given by the children of this object.
public class TargetPoints : MonoBehaviour {
    public IEnumerable<Vector3> Positions =>
        transform.Cast<Transform>().Select(child => child.position);
}
