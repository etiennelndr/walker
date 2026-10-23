using System;

// Identifier of the current run of the simulation, shared by all the walkers. It is generated
// once per domain reload, i.e. each time the Play mode is entered with the default editor
// settings, or each time a built player starts.
public static class Session {
    public static readonly string Id = Guid.NewGuid().ToString();
}
