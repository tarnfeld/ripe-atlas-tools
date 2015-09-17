from tzlocal import get_localzone
from .base import Report


class DnsReport(Report):

    TIME_FORMAT = "%a %b %d %H:%M:%S %Z %Y"

    def format(self, result):

        # We're not currently handling multiple responses because it's hard
        response = result.responses[0]
        created = result.created.astimezone(get_localzone())

        if not response.abuf:
            return "\nProbe #{}\n{}\nNo abuf found\n\n".format(
                result.probe_id,
                "=" * 79,
            )

        header_flags = []
        for flag in ("aa", "ad", "cd", "qr", "ra", "rd",):
            if getattr(response.abuf.header, flag):
                header_flags.append(flag)

        edns = ""
        if response.abuf.edns0:
            edns = ";; OPT PSEUDOSECTION:\n; EDNS: version: {}, flags:; udp: {}".format(
                response.abuf.edns0.version,
                response.abuf.edns0.udp_size
            )

        return self.render(

            "reports/dns.txt",

            probe=result.probe_id,

            question_name=response.abuf.questions[0].name,
            header_opcode=response.abuf.header.opcode,
            header_return_code=response.abuf.header.return_code,
            header_id=response.abuf.header.id,
            header_flags=" ".join(header_flags),
            edns=edns,

            question_count=len(response.abuf.questions),
            answer_count=len(response.abuf.answers),
            authority_count=len(response.abuf.authorities),
            additional_count=len(response.abuf.additionals),

            question=self.get_section(
                "question", response.abuf.questions),
            answers=self.get_section(
                "answer", response.abuf.answers),
            authorities=self.get_section(
                "authority", response.abuf.authorities),
            additionals=self.get_section(
                "additional", response.abuf.additionals),

            response_time=response.response_time,
            response_size=response.response_size,
            created=created.strftime(self.TIME_FORMAT),
            destination_address=response.destination_address,

        )

    @staticmethod
    def get_section(header, data):

        if not data:
            return ""

        return "\n\n;; {} SECTION:\n".format(
            header.upper()) + "\n".join([str(_) for _ in data]) + "\n"
