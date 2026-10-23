namespace Api.Models {
    public class Error : ApiModel<Error> {
        public int status;
        public string message;
        public string code;
    }
}
